def get_cur_from_data_path(cur, out, data_path):
    from string import split
    dp_parts = split(data_path, '/')
    if dp_parts[0] == '':
        if len(dp_parts) < 2:
            return cur
        start = out
        dp_parts = dp_parts[1:]
    else:
        start = cur
        pass
    
    for part in dp_parts:
        if part == '':
            continue
        if isinstance(cur, (tuple, list)):
            cur = cur[int(part)]
        else:
            cur = cur[part]
            pass
        pass
    return cur

def formalize_out(out):
    queue = [out]
    while len(queue):
        cur = queue.pop()
        for key, child in cur.items():
            if isinstance(child, dict):
                if key == '..':
                    continue
                child['..'] = cur
                queue.append(child)
            elif isinstance(child, (tuple, list)):
                children = child
                for child in children:
                    if isinstance(child, dict):
                        child['..'] = cur
                        queue.append(child)
                        pass
                    pass
                pass
            pass
        pass
    pass
