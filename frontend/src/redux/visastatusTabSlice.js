import { createSlice } from "@reduxjs/toolkit";
import { getCookie, setCookie } from "../utils/cookie";

const visastatusTabSlice = createSlice({
    name: "visastatusTab",
    initialState: getCookie("visaType", "F"),
    reducers: {
        changeTab: (state, action) => {
            setCookie("visaType", action.payload.activeKey);
            return action.payload.activeKey;
        },
    },
});

const { reducer, actions } = visastatusTabSlice;
export const { changeTab } = actions;
export default reducer;
