from csamoa.util import queryset_foreach

def serialize_qs4e(serializer, querysets, stream, **options):
    qs4e_options = {'transaction': False, 'batch_size': 50}
    for opt in ['batch_size', 'progress_callback', 'transaction']:
        val = options.pop(opt, None)
        if val is not None: qs4e_options[opt] = val

    serializer.options = options
    serializer.options['stream'] = stream
    serializer.stream = stream
    serializer.selected_fields = options.get("fields")

    def serialize_object(obj):
        #import pdb; pdb.set_trace()

        serializer.start_object(obj)
        for field in obj._meta.local_fields:
            if field.serialize:
                if field.rel is None:
                    if serializer.selected_fields is None or field.attname in serializer.selected_fields:
                        serializer.handle_field(obj, field)
                else:
                    if serializer.selected_fields is None or field.attname[:-3] in serializer.selected_fields:
                        serializer.handle_fk_field(obj, field)
        for field in obj._meta.many_to_many:
            if field.serialize:
                if serializer.selected_fields is None or field.attname in serializer.selected_fields:
                    serializer.handle_m2m_field(obj, field)
        serializer.end_object(obj)

    serializer.start_serialization()
    for queryset in querysets:
        queryset_foreach(queryset, serialize_object, **qs4e_options)
    serializer.end_serialization()

