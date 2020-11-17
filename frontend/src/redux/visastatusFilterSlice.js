import { createSlice } from "@reduxjs/toolkit";

const visastatusFilterSlice = createSlice({
    name: "visastatusFilter",
    initialState: { F: [], B: [], O: [], H: [], L: [] },
    reducers: {
        updateFilter: (state, action) => {
            const { visaType, newFilter } = action.payload;
            state[visaType] = newFilter;
        },
    },
});

const { reducer, actions } = visastatusFilterSlice;
export const { updateFilter } = actions;
export default reducer;
