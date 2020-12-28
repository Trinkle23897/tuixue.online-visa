const snakeToCamel = str => str.replace(/_(.)/g, s => s[1].toUpperCase());

export const renameObjectKeys = obj => {
    if (typeof obj !== "object" || obj === null) {
        return obj;
    }

    if (Array.isArray(obj)) {
        return obj.map(o => renameObjectKeys(o));
    }

    return Object.fromEntries(Object.entries(obj).map(([key, val]) => [snakeToCamel(key), renameObjectKeys(val)]));
};

/**
 * Extract the year, month date from datetime string
 * Not using javascript's Date class cause it sucks at datetime string parsing
 * @param {string} s ISO Datetime string in format of `YYYY-MM-DDTHH:MM:SS`
 */
export const getDateFromISOString = s => s.split("T")[0].split("-");
export const getTimeFromISOString = s =>
    s
        .split("T")[1]
        .split(":")
        .map(i => i.split(".")[0]);

export const getLocalDateTimeFromISOString = s => {
    const date = new Date(Date.UTC(...getDateFromISOString(s), ...getTimeFromISOString(s)));
    return [
        date.getFullYear(),
        date.getMonth() + 1,
        date.getDate(),
        date.getHours(),
        date.getMinutes(),
        date.getSeconds(),
    ].map(o => o.toString().padStart(2, "0"));
};
