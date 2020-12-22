import { createSlice } from "@reduxjs/toolkit";
import { getCookie, setCookie } from "../utils/cookie";

const visastatusTabSlice = createSlice({
    name: "visastatusTab",
    initialState: getCookie("visaType", "F"),
    reducers: {
        changeTab: (state, action) => {
            return action.payload.activeKey;
        },
    },
});

const { reducer, actions } = visastatusTabSlice;
const { changeTab } = actions;
export const changeTabAndSetCookie = activeKey => async dispatch => {
    setCookie("visaType", activeKey);
    dispatch(changeTab({ activeKey }));
    return Promise.resolve();
};

export default reducer;
