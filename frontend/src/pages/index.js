import React from "react";
import { BrowserRouter as Router, Switch, Route, Redirect } from "react-router-dom";
import VisaStatus from "./VisaStatus";
import Subscription from "./Subscription";

export default function Pages() {
    return (
        <Router>
            <Switch>
                <Route exact path="/visa" component={() => <VisaStatus />} />
                <Route exact path="/visa/email/:subscriptionOp" component={() => <Subscription />} />
                <Redirect to="/visa" />
            </Switch>
        </Router>
    );
}
