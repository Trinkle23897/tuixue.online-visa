import { createSlice } from "@reduxjs/toolkit";
import { getDateFromISOString } from "../utils/misc";

const visastatusNewestSlice = createSlice({
    name: "latestWritten",
    initialState: Array.from("FJBOHL").reduce((obj, vt) => ({ ...obj, [vt]: {} }), {}),
    reducers: {
        updateNewest: (state, action) => {
            const { visaType, newest } = action.payload;
            newest.forEach(({ embassyCode, availableDate, writeTime }) => {
                state[visaType][embassyCode] = {
                    availableDate: availableDate ? getDateFromISOString(availableDate) : ["/"],
                    writeTime,
                };
            });
        },
    },
});

const { reducer, actions } = visastatusNewestSlice;

export const { updateNewest } = actions;

export default reducer;
