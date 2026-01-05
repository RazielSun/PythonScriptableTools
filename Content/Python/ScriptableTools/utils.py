import unreal as ue


def create_delegate(delegate_class, function):
    delegate = delegate_class()
    delegate.bind_callable(function)
    return delegate


def break_hit_result(hit: ue.HitResult) -> dict:
    blocking_hit, initial_overlap, time, distance, location, impact_point, normal, impact_normal, phys_mat, hit_actor, hit_component, hit_bone_name, bone_name, hit_item, element_index, face_index, trace_start, trace_end = hit.to_tuple()
    result = {
        "blocking_hit": blocking_hit,
        "initial_overlap": initial_overlap,
        "time": time,
        "distance": distance,
        "location": location,
        "impact_point": impact_point,
        "normal": normal,
        "impact_normal": impact_normal,
        "phys_mat": phys_mat,
        "hit_actor": hit_actor,
        "hit_component": hit_component,
        "hit_bone_name": hit_bone_name,
        "bone_name": bone_name,
        "hit_item": hit_item,
        "element_index": element_index,
        "face_index": face_index,
        "trace_start": trace_start,
        "trace_end": trace_end,
    }
    return result