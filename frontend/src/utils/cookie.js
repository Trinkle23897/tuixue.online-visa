import Cookies from "js-cookie";

export const setCookie = (name, value) => {
    Cookies.set(name, value);
};

export const getCookie = (name, defaultValue) => {
    const value = Cookies.get(name) || defaultValue;
    return typeof defaultValue === typeof value ? value : JSON.parse(value);
};
