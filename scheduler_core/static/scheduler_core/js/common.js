function getCookie(cookieName) {
    var name = cookieName + "=";
    var cookieArguments = document.cookie.split(';');

    for (var i = 0; i < cookieArguments.length; i++) {
        var c = cookieArguments[i];

        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }

        if (c.indexOf(name) == 0) {
            // return true or false.
            return c.substring(name.length, c.length);
        }
    }

    return "";
}