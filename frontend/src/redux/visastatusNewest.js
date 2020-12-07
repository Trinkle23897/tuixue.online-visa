import { createSlice } from "@reduxjs/toolkit";
import { getDateFromISOString, getTimeFromISOString } from "../utils/misc";

const visastatusNewest = createSlice({
    name: "latestWritten",
    initialState: Array.from("FBOHL").reduce((obj, vt) => ({ ...obj, [vt]: {} }), {}),
    reducers: {
        updateNewest: (state, action) => {
            const { visaType, newest } = action.payload;
            newest.forEach(({ embassyCode, availableDate, writeTime }) => {
                state[visaType][embassyCode] = {
                    availableDate: availableDate ? getDateFromISOString(availableDate) : ["/"],
                    writeTime: [...getDateFromISOString(writeTime), ...getTimeFromISOString(writeTime)],
                };
            });
        },
    },
});

const { reducer, actions } = visastatusNewest;

export const { updateNewest } = actions;

export default reducer;
