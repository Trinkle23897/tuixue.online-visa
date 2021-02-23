import React from "react";
import PropTypes from "prop-types";
import { Typography, Row, Col } from "antd";
import { useTranslation } from "react-i18next";
import { CheckCircleTwoTone, CloseCircleTwoTone, LoadingOutlined } from "@ant-design/icons";

export default function PostSubscriptionResult({ success, step, inEmailPage }) {
    const [t] = useTranslation();
    const successText = t(`emailForm.successText.${step}`);
    const failureText = t("emailForm.failureText");
    const loadingText = t("emailForm.loadingText");

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
                    {success === null ? loadingText : success ? successText : failureText}
                </Typography.Title>
            </Col>
            <Col>
                <Typography.Text style={{ textAlign: "center", fontStyle: "italic" }}>
                    {t(inEmailPage ? "emailForm.redirecting" : "emailForm.closing")}
                </Typography.Text>
            </Col>
        </Row>
    );
}
PostSubscriptionResult.propTypes = {
    success: PropTypes.bool.isRequired,
    step: PropTypes.oneOf(["confirming", "subscribed", "deleted"]).isRequired,
    inEmailPage: PropTypes.bool.isRequired,
};
