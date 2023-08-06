##parameters=macro,**kw

if same_type(macro, 'str'):
    if not kw.has_key('template'):
        raise "template is a required keyword argument"

    template = kw['template']
    if same_type(template, 'str'):
        template_id = template
        template = context.restrictedTraverse(template_id)
    else:
        template_id = template.getId()

    extra_context = {'the_template_path':'context/%s' % template_id, 
        'macro':macro,
        'the_template':template,
        'options':{'template_id':template_id},
        }
    extra_context.update(kw)
    if not extra_context['options'].has_key('template_id'):
        extra_context['options']['template_id'] = template_id
else:
    extra_context = {'macro':macro}
    extra_context.update(kw)


return context.kssinline_macro_renderer.pt_render(extra_context=extra_context).strip()
