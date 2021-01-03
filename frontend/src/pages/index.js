import React from "react";
import { BrowserRouter as Router, Switch, Route, Redirect } from "react-router-dom";
import VisaStatus from "./VisaStatus";
import Subscription from "./Subscription";

export default function Pages() {
    return (
        <Router>
            <Switch>
                <Route exact path="/" component={() => <VisaStatus />} />
                <Route exact path="/subscription/email" component={() => <Subscription />} />
                <Redirect to="/" />
            </Switch>
        </Router>
    );
}
