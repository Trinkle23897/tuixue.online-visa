import { createSlice } from "@reduxjs/toolkit";
import { getSingleVisaStatus } from "../services";
import { getDateFromISOString } from "../utils/misc";

const visastatusDetailSlice = createSlice({
    name: "visastatusDetail",
    initialState: { F: {}, B: {}, O: {}, H: {}, L: {} },
    reducers: {
        updateDeatil: (state, action) => {
            const { visaType, embassyCode, availableDates } = action.payload;
            state[visaType][embassyCode] = availableDates;
        },
    },
});

const { reducer, actions } = visastatusDetailSlice;
export const { updateDeatil } = actions;

export const fetchVisaStatusDetail = (visaType, embassyCode) => async (dispatch, getState) => {
    const {
        visastatusDetail: { [visaType]: selectEmb },
    } = getState();
    if (embassyCode in selectEmb) {
        return Promise.resolve();
    }
    try {
        const vsDetail = await getSingleVisaStatus(visaType, embassyCode, new Date());
        if (vsDetail) {
            const { availableDates: avaiDates } = vsDetail;
            const availableDates = avaiDates.map(({ writeTime, availableDate }) => ({
                writeTime,
                availableDate: availableDate === null ? null : getDateFromISOString(availableDate),
            }));
            dispatch(updateDeatil({ visaType, embassyCode, availableDates }));
        }
    } catch (e) {
        console.error(`In fetchVisaStatusDetail: ${e}`);
    }

    return Promise.resolve();
};

export default reducer;
