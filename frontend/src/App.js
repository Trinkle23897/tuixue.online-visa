import React, { useEffect } from "react";
import { Provider } from "react-redux";
import store from "./redux";
import Pages from "./pages";
import { VisaStatusNotification } from "./components";
import { useInitialDataFetch } from "./hooks";
import "./assets/styles/index.less";

let RENDER_TIME = 0; // for debug purpose delete before production

function App() {
    useInitialDataFetch();

    useEffect(() => {
        RENDER_TIME += 1;
        console.log(`Render the whole page ${RENDER_TIME}`);
    });

    return (
        <>
            <Pages />
            <VisaStatusNotification />
        </>
    );
}

export default () => (
    <Provider store={store}>
        <App />
    </Provider>
);
