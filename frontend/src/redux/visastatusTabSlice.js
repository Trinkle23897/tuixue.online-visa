import { createSlice } from "@reduxjs/toolkit";

const visastatusTabSlice = createSlice({
    name: "visastatusTab",
    initialState: "F", // TODO: read historical preference from cookie
    reducers: {
        changeTab: (state, action) => action.payload.activeKey,
    },
});

const { reducer, actions } = visastatusTabSlice;
export const { changeTab } = actions;
export default reducer;
