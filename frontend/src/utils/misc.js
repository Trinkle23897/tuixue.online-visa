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
