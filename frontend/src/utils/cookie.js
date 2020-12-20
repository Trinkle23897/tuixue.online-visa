import Cookies from "js-cookie";

export const setCookie = (name, value) => {
    Cookies.set(name, value);
};

export const getCookie = (name, defaultValue) => {
    let value = Cookies.get(name) || defaultValue;
    if (!(typeof defaultValue === typeof value)) {
        // js-cookie stores array as string
        value = JSON.parse(value);
    }
    return value;
};
