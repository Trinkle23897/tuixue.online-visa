import { createSlice } from "@reduxjs/toolkit";
import { getSingleVisaStatus } from "../services";
import { getDateFromISOString, getTimeFromISOString } from "../utils/misc";

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

export const fetchVisaStatusDetail = (visaType, embassyCode) => async dispatch => {
    try {
        const vsDetail = await getSingleVisaStatus(visaType, embassyCode, new Date());
        if (vsDetail) {
            const { availableDates: avaiDates } = vsDetail;
            const availableDates = avaiDates.map(({ writeTime, availableDate }) => ({
                writeTime: [...getDateFromISOString(writeTime), ...getTimeFromISOString(writeTime).slice(0, -1), "00"],
                availableDate: getDateFromISOString(availableDate),
            }));
            dispatch(updateDeatil({ visaType, embassyCode, availableDates }));
        }
    } catch (e) {
        console.error(`In fetchVisaStatusDetail: ${e}`);
    }

    return Promise.resolve();
};

export default reducer;
