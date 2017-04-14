from django import template

register = template.Library()


@register.inclusion_tag('scheduler_core/schedule_tag.html', takes_context=True)
def show_schedule(context):
    """ Show schedule for a movie. """
    program = context['program']

    return {'program': program}
