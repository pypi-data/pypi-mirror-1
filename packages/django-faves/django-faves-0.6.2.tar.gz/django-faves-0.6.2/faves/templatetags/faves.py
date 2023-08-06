import datetime

from django import template
from django.template import Library, Node
from django.contrib.contenttypes.models import ContentType
from django.template import resolve_variable
from django.core.urlresolvers import reverse
from django.db import models

register = Library()

Fave = models.get_model('faves', 'fave')
FaveType = models.get_model('faves', 'favetype')


def validate_template_tag_params(bits, arguments_count, keyword_positions):
    '''
        Raises exception if passed params (`bits`) do not match signature.
        Signature is defined by `bits_len` (acceptible number of params) and
        keyword_positions (dictionary with positions in keys and keywords in values,
        for ex. {2:'by', 4:'of', 5:'type', 7:'as'}).            
    '''    
    
    if len(bits) != arguments_count+1:
        raise template.TemplateSyntaxError("'%s' tag takes %d arguments" % (bits[0], arguments_count,))
    
    for pos in keyword_positions:
        value = keyword_positions[pos]
        if bits[pos] != value:
            raise template.TemplateSyntaxError("argument #%d to '%s' tag must be '%s'" % (pos, bits[0], value))
        
    
@register.filter
def has_faved(value, arg):
    """
    Returns True if user have faved passed object and False otherwise.
    Example:
        {% if request.user|has_faved:object %}
        ...
    """
    user = value
    object = arg
    try:
        fave = Fave.objects.get_for_model(object).get(user=user, object_id=object.id, withdrawn=False)
    except Fave.DoesNotExist:
        return False
    
    return True


@register.filter('is_favorited')
def is_favorited(value, arg):
    try:
        return value.id in arg
    except:
        return False
    

@register.simple_tag
def get_toggle_fave_url(object, fave_type_slug='favorites'):
    """
    Given an object, returns the URL for "toggle favorite for this item".
    Optionally takes a second argument, which is the slug of a 
    FaveType object. If this is provided, will return the URL for
    that FaveType. If not, will use the first FaveType (which, by
    default, is "Favorite".)
    
    Example usage:
    
    {% load faves %}
    <p><a href="{% get_toggle_fave_url photo favorites %}">{% if request.user|has_faved:photo %}Unfavorite{% else %}Favorite{% endif %} this photo</a></p>

    """
    try:        
        content_type = ContentType.objects.get_for_model(object)
        return reverse('toggle_fave', args=(fave_type_slug, content_type.id, object.id))
    except:
        return ''


@register.simple_tag
def get_fave_url(object, fave_type_slug='favorites'):
    """
    Given an object, returns the URL for "favorite this item".
    Optionally takes a second argument, which is the slug of a 
    FaveType object. If this is provided, will return the URL for
    that FaveType. If not, will use the first FaveType (which, by
    default, is "Favorite".)
    
    Example usage:
    
    {% load faves %}
    {% if request.user|has_faved:photo %}
        <p><a href="{% get_unfave_url photo favorites %}">Unfavorite this photo</a></p>
    {% else %}
        <p><a href="{% get_fave_url photo favorites %}">Favorite this photo</a></p>
    {% endif %}
    
    """
    try:
        content_type = ContentType.objects.get_for_model(object)
        return reverse('fave_object', args=(fave_type_slug, content_type.id, object.id))
    except:
        return ''

@register.simple_tag
def get_unfave_url(object, fave_type_slug='favorites'):
    """
    Given an object, returns the URL for "unfavorite this item."
    Optionally takes a second argument, which is the slug of a 
    FaveType object. If this is provided, will return the URL for
    that FaveType. If not, will default to the first FaveType (which,
    by default, is "Favorite".)
    
    Example usage:
    
    {% load faves %}
    {% get_fave by user on photo of type favorites as fave %}
    {% if fave %}
        <p><a href="{% get_unfave_url photo 'favorites' %}">Unfavorite this photo</a></p>
    {% else %}
        <p><a href="{% get_fave_url photo 'favorites' %}">Favorite this photo</a></p>
    {% endif %}
    """
    try:
        content_type = ContentType.objects.get_for_model(object)
        return reverse('unfave_object', kwargs={'fave_type_slug': fave_type_slug, 
                                                'content_type_id': content_type.id,
                                                'object_id': object.id})
    except:
        return ''



class GetFavoritesForUserNode(template.Node):
    def __init__(self, user, fave_type_slug, model, varname):
        self.user, self.fave_type_slug, self.model, self.varname = user, fave_type_slug, model, varname

    def render(self, context):
        try:
            user = resolve_variable(self.user, context)
            if self.model:
                [app_label, model_name] = model.split('.')
                content_type = ContentType.objects.get(app_label=app_label, model=model_name)
                context[self.varname] = Fave.objects.active().filter(type__slug=self.fave_type_slug, user=user, content_type=content_type)
            else:    
                context[self.varname] = Fave.objects.active().filter(type__slug=self.fave_type_slug, user=user)
        except:
            pass
        return ''

@register.tag
def get_faves_for_user(parser, token):
    """
    
    Retrieves user's favorites of specified relation type (and possibly content-type) and assigns it to a context variable.
    
    Syntax::

        {% get_faves_for_user [user] of type [fave-type-slug] [?model] as [varname] %}

    Example::

        {% get_faves_for_user user of type favorites as faves %}
        {% get_faves_for_user user of type favorites comments.comment as faves %}

    """
    bits = token.contents.split()
    if len(bits) not in [7,8]:
        raise template.TemplateSyntaxError("'%s' tag takes six or seven arguments" % bits[0])
    if bits[2] != 'of':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'of'" % bits[0])
    if bits[3] != 'type':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'type'" % bits[0])
    if bits[5] != 'as' and bits[6] != 'as':
        raise template.TemplateSyntaxError("fifth or sixth argument to '%s' tag must be 'as'" % bits[0])
    
    if bits[5] == 'as': #all content types
        return GetFavoritesForUserNode(bits[1], bits[4], None, bits[6])
    else: # only specified content type
        return GetFavoritesForUserNode(bits[1], bits[4], bits[5], bits[7])


class GetFavoritedNode(template.Node):
    def __init__(self, object_list, user, fave_type_slug, varname):
        self.object_list, self.user, self.fave_type_slug, self.varname = object_list, user, fave_type_slug, varname
        
    def return_results(self):
        context[self.varname] = self.faves_dict

    def render(self, context):
        try:
            user = resolve_variable(self.user, context)
            self.objects = resolve_variable(self.object_list, context)                         

            ''' allow single object to be passed by putting it into list '''
            try:  
                it = iter(self.objects)
            except TypeError: 
                self.objects = [self.objects]
                
            content_type = ContentType.objects.get_for_model(self.objects[0])
            
            faves = Fave.objects.active().filter(type__slug=self.fave_type_slug, 
                                                 user=user, 
                                                 content_type=content_type,
                                                 object_id__in=[item.id for item in self.objects])            
            self.faves_dict = dict((fave.object_id, fave) for fave in list(faves))            
            
            self.return_results()
        except:
            pass
        return ''

@register.tag
def get_favorited(parser, token):
    """
    Makes dict::
    
        {
            <object_id1>: <Fave object1>, 
            <object_id2>: <Fave object1>,             
            ...
        }
        
    and assigns it to a context variable. Keys are id's of favorited objects, values are Fave model instances.
    
    Syntax::

        {% get_favorited [objects] by [user] of type [fave-type-slug] as [varname] %}

    Example::

        {% get_favorited page.object_list by request.user of type favorites as faves %}
        
    `objects` is an iterable with django models.

    """
    bits = token.contents.split()
    validate_template_tag_params(bits, 8, {2:'by', 4:'of', 5:'type', 7:'as'})
                
    return GetFavoritedNode(bits[1], bits[3], bits[6], bits[8])



class InjectFavesToNode(GetFavoritedNode):
    def return_results(self):
        for object in self.objects:
            if self.faves_dict.has_key(object.id):
                object.__setattr__(self.varname, self.faves_dict[object.id])        

@register.tag
def inject_faves_to(parser, token):
    """
    Adds attribute with Fave instance for each favorited object in `objects` list (iterable with django models)  
    
    Syntax::

        {% inject_faves_to [objects] by [user] of type [fave-type-slug] as [attribute_name] %}

    Example::

        {% inject_faves_to page.object_list by request.user of type favorites as fave %}
        
        {% for object in page.object_list %}
            {{ object }}
            {% if object.fave %}
                favorited 
            {% endif %}
        {% endfor %}
        
    """
    bits = token.contents.split()    
    validate_template_tag_params(bits, 8, {2:'by', 4:'of', 5:'type', 7:'as'})
                
    return InjectFavesToNode(bits[1], bits[3], bits[6], bits[8])



class GetFavoriteNode(template.Node):
    def __init__(self, user, object, fave_type_slug, varname):
        self.user, self.object, self.fave_type_slug, self.varname = user, object, fave_type_slug, varname

    def render(self, context):
        try:
            user = resolve_variable(self.user, context)
            object = resolve_variable(self.object, context)
            content_type = ContentType.objects.get_for_model(object)
            try:
                fave = Fave.active_objects.get(type__slug=self.fave_type_slug, user=user, content_type=content_type, object_id=object.id)
            except:
                fave = None
            context[self.varname] = fave
        except:
            pass
        return ''
    


@register.tag
def get_fave(parser, token):
    """
    Syntax::
        {% get_fave by [user] on [object] of type [fave-type-slug] as [varname] %}

    Example::
        {% get_fave by user on photo of type favorites as fave %}

    """
    bits = token.contents.split()
    validate_template_tag_params(bits, 9, {1:'by', 3:'on', 5:'of', 6:'type', 8:'as'})
    
    return GetFavoriteNode(bits[2], bits[4], bits[7], bits[9])
