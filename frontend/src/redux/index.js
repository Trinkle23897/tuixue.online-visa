import { configureStore } from "@reduxjs/toolkit";
import metadata from "./metadataSlice";
import visastatusNewest from "./visastatusNewest";
import visastatusFilter from "./visastatusFilterSlice";
import visastatusOverview from "./visastatusOverviewSlice";
import visastatusTab from "./visastatusTabSlice";
import language from "./languageSlice";

export default configureStore({
    reducer: {
        metadata,
        language,
        visastatusNewest,
        visastatusFilter,
        visastatusOverview,
        visastatusTab,
    },
});
