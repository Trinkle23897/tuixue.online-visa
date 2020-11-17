import { createSlice } from "@reduxjs/toolkit";

const visastatusNewest = createSlice({
    name: "latestWritten",
    initialState: Array.from("FBOHL").reduce((obj, vt) => ({ ...obj, [vt]: { previous: [], current: [] } }), {}),
    reducers: {
        updateNewest: (state, action) => {
            const { visaType, current } = action.payload;
            [state[visaType].previous, state[visaType].current] = [state[visaType].current, current];
        },
    },
});

const { reducer, actions } = visastatusNewest;

export const { updateNewest } = actions;

export default reducer;
