import { configureStore } from "@reduxjs/toolkit";
import metadata from "./metadataSlice";
import visastatusNewest from "./visastatusNewest";
import visastatusFilter from "./visastatusFilterSlice";
import visastatusOverview from "./visastatusOverviewSlice";

export default configureStore({
    reducer: {
        metadata,
        visastatusNewest,
        visastatusFilter,
        visastatusOverview,
    },
});
