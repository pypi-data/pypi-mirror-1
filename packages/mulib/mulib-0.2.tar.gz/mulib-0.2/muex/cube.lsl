
integer running;
string server = "http://donovanpreston.com:8080/cube/";
string r_etag = "";
string g_etag = "";
string b_etag = "";


integer make_request() {
    llHTTPRequest(
        server,
        [HTTP_METHOD, "POST", 
        HTTP_MIMETYPE, "text/plain"],
        "{\"client-id\": \"" +
        (string)llGetOwner() +
        "\", \"observe\": [{\"path\": \"r\", \"etag\": \"" + r_etag +
        "\"}, {\"path\": \"g\", \"etag\": \"" + g_etag + 
        "\"}, {\"path\": \"b\", \"etag\": \"" + b_etag +
        "\"}]}");
    return 0;
}


integer handle_event(string path, string body, string etag) {
    vector my_color = llGetColor(ALL_SIDES);
    float new_val = (float)body;
    if(path == "r") {
        my_color.x = new_val;
        r_etag = etag;
    } else if (path == "g") {
        my_color.y = new_val;
        g_etag = etag;
    } else if (path == "b") {
        my_color.z = new_val;
        b_etag = etag;
    }
    llSetColor(my_color, ALL_SIDES);
    return 0;
}

default
{
    state_entry()
    {
    }

    touch_start(integer total_number)
    {
        if (llDetectedKey(0) != llGetOwner()) {
            return;   
        }
        if (!running) {
            llOwnerSay("Connecting");
            make_request();   
        } else {
            llOwnerSay("Disconnecting");
        }
        running = !running;
    }

    http_response(key request_id, integer status, list metadata, string raw_body)
    {
        string path;
        string body;
        string etag;
        if (status != 202) {
            // do stuff
            list l = llParseString2List(raw_body, ["|", "\n"], []);
            integer i;
            for (i = 0; i < llGetListLength(l); i += 2) {
                string k = llList2String(l, i);
                string v = llList2String(l, i+1);
                if (k == "path") {
                    path = v;   
                } else if (k == "body") {
                    body = v;
                } else if (k == "etag") {
                    etag = v;
                }
            }
        }
        llOwnerSay((string) status + " " + path + " " + body);
        if (status == 500 || status == 502 || status == 503 || status == 404 || status == 301) {
            running = 0;
        }
        if (running) {
            handle_event(path, body, etag);
            make_request();
        }
    }
}
