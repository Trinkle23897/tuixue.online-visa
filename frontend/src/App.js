import React, { useEffect } from "react";
import { Provider } from "react-redux";
import ReactGA from "react-ga";
import store from "./redux";
import Pages from "./pages";
import { VisaStatusNotification } from "./components";
import { useInitialDataFetch, useScript } from "./hooks";
import "./assets/styles/index.less";

let RENDER_TIME = 0; // for debug purpose delete before production

function App() {
    ReactGA.initialize("UA-102409527-2");
    ReactGA.pageview(window.location.pathname + window.location.search);
    useInitialDataFetch();
    useScript("https://busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js");

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
