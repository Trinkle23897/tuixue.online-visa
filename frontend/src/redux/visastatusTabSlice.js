import { createSlice } from "@reduxjs/toolkit";
import { getCookie, setCookie } from "../utils/cookie";
import { fetchVisaStatusDetail } from "./visastatusDetailSlice";
import { fetchVisaStatusOverview } from "./visastatusOverviewSlice";

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
    dispatch(fetchVisaStatusOverview(activeKey));
    dispatch(fetchVisaStatusDetail(activeKey));
    return Promise.resolve();
};

export default reducer;
