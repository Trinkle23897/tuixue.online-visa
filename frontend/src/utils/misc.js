import fromEntries from "fromentries";
import moment from "moment";

const snakeToCamel = str => str.replace(/_(.)/g, s => s[1].toUpperCase());

export const renameObjectKeys = obj => {
    if (typeof obj !== "object" || obj === null) {
        return obj;
    }

    if (Array.isArray(obj)) {
        return obj.map(o => renameObjectKeys(o));
    }

    return fromEntries(Object.entries(obj).map(([key, val]) => [snakeToCamel(key), renameObjectKeys(val)]));
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

export const getTimeFromUTC = u => {
    const date = new Date(u);
    return [date.getHours(), date.getMinutes(), date.getSeconds()].map(o => o.toString().padStart(2, "0"));
};

export const dateDiff = (start, end) => {
    return end ? (new Date(end) - new Date(start)) / 86400000 : null;
};

/**
 * Convert a moment object to ISO string using the year, month, day part. moment().format() output is actually
 * local time, but we treat the [year, month, day] as UTC date for practical purpose.
 *
 * @param {moment} mnt the moment.js object.
 * @returns {string} The ISO formatted string.
 */
export const momentToISOString = mnt => new Date(Date.UTC(mnt.year(), mnt.month(), mnt.date())).toISOString();

/**
 * Convert an ISOString to momentjs object using it's [year, month, day] part. P.S. moment(Number[]) with return
 * a object with [year, month, day] as local time.
 *
 * @param {string} isoString ISO formatted datetime string
 * @returns {moment} The momentjs object
 */
export const isoStringToMoment = isoString => {
    const utc = new Date(Date.parse(isoString));
    return moment([utc.getUTCFullYear(), utc.getUTCMonth(), utc.getUTCDate()]);
};

/**
 * Imperfect mimic of python `zip` function
 *
 * @param  {...any[]} sequences Arrays for zipping
 * @returns {...any[][]} Zipped array
 */
export const zip = (...sequences) => [...sequences[0]].map((_, idx) => sequences.map(seq => seq[idx]));
