import { createSlice } from "@reduxjs/toolkit";
import { getVisaStatusOverview } from "../services";

const visastatusOverviewSlice = createSlice({
    name: "visastatusOverview",
    initialState: { F: [], B: [], O: [], H: [], L: [] },
    reducers: {
        updateOverview: (state, action) => {
            const { visaType, visaStatus } = action.payload;
            state[visaType] = visaStatus;
        },
    },
});

const { reducer, actions } = visastatusOverviewSlice;
export const { updateOverview } = actions;

export const fetchVisaStatusOverview = visaType => async (dispatch, getState) => {
    const {
        visastatusFilter: { [visaType]: selectedEmb },
    } = getState();

    if (selectedEmb.length === 0) {
        return Promise.resolve();
    }

    const now = new Date();
    try {
        const vsOverview = await getVisaStatusOverview(visaType, selectedEmb, now, now);
        if (vsOverview) {
            const { visaStatus } = vsOverview;
            dispatch(updateOverview({ visaType, visaStatus }));
        }
    } catch (e) {
        console.error(`In fetchVisaStatusOverview: ${e}`);
    }

    return Promise.resolve();
};

export const fetchAllOverview = () => async (dispatch, getState) => {
    const { visastatusFilter: vsFilter } = getState();
    const visaTypes = Object.keys(vsFilter).filter(vt => vsFilter[vt].length > 0);
    const embassyCodes = [...new Set(Object.values(vsFilter).flat())];

    const now = new Date(Date.now());
    try {
        const allOverview = await getVisaStatusOverview(visaTypes, embassyCodes, now, now);
        console.log(allOverview);
        if (allOverview) {
            const { visa_status: visaStatus } = allOverview;
            visaTypes.forEach(vt => dispatch(updateOverview({ visaType: vt, visaStatus })));
        }
    } catch (e) {
        console.error(`In fetchAllOverview: ${e}`);
    }

    return Promise.resolve();
};

export default reducer;
