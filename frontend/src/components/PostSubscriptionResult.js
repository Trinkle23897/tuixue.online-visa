import React from "react";
import PropTypes from "prop-types";
import { Typography, Row, Col } from "antd";
import { CheckCircleTwoTone, CloseCircleTwoTone, LoadingOutlined } from "@ant-design/icons";

export default function PostSubscriptionResult({ success, step, inSubscriptionPage }) {
    const successText = {
        confirming: "Subscription request sent. Please check your email.",
        subscribed: "Successfully subscribed. Thank you!",
    };
    const failureText = "Something goes wrong, we are sorry. Please try again.";
    const loadingText = "We are processing your subscription";

    return (
        <Row justify="center" align="middle" gutter={[16, { xs: 16, md: 32 }]}>
            <Col>
                {success === null ? (
                    <LoadingOutlined style={{ fontSize: "48px" }} />
                ) : success ? (
                    <CheckCircleTwoTone twoToneColor="#52c41a" style={{ fontSize: "48px" }} />
                ) : (
                    <CloseCircleTwoTone twoToneColor="#f5222d" style={{ fontSize: "48px" }} />
                )}
            </Col>
            <Col span={24}>
                <Typography.Title level={3} style={{ textAlign: "center" }}>
                    {success === null ? loadingText : success ? successText[step] : failureText}
                </Typography.Title>
            </Col>
            <Col>
                <Typography.Text style={{ textAlign: "center", fontStyle: "italic" }}>
                    {inSubscriptionPage ? "Redirecting to home page in 3 seconds..." : "Closing in 3 seconds..."}
                </Typography.Text>
            </Col>
        </Row>
    );
}
PostSubscriptionResult.propTypes = {
    success: PropTypes.bool.isRequired,
    step: PropTypes.oneOf(["confirming", "subscribed"]).isRequired,
    inSubscriptionPage: PropTypes.bool.isRequired,
};
