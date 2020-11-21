import { createSlice } from "@reduxjs/toolkit";

const visastatusNewest = createSlice({
    name: "latestWritten",
    initialState: Array.from("FBOHL").reduce((obj, vt) => ({ ...obj, [vt]: [] }), {}),
    reducers: {
        updateNewest: (state, action) => {
            const { visaType, newest } = action.payload;
            state[visaType] = newest;
        },
    },
});

const { reducer, actions } = visastatusNewest;

export const { updateNewest } = actions;

export default reducer;
