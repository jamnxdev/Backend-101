def parse_request(raw_bytes):
    try:
        text = raw_bytes.decode()
    except UnicodeDecodeError:
        return None

    lines = text.split("\r\n")
    if not lines:
        return None
    
    try:
        method, path, version = lines[0].split()
    except ValueError:
        return None
    
    headers = {}
    for line in lines[1:]:
        if line == "":
            break
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        headers[k.strip()] = v.strip()

    return {
        "method": method,
        "path": path,
        "version": version,
        "headers": headers,
        "raw": raw_bytes
    }