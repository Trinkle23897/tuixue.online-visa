import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { HashLink as Link } from "react-router-hash-link";
import { Row, Col, Button, Layout, Menu, Popover } from "antd";
import { MenuOutlined, CloseOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { IoLanguageOutline } from "react-icons/io5";
import { useScreenXS } from "../hooks";
import { setCookie } from "../utils/cookie";
import "./TuixueHeader.less";

const { Header } = Layout;

const NavMenu = ({ mode, theme, onClick }) => {
    const [t] = useTranslation();
    return (
        <Menu theme={theme} mode={mode} onClick={onClick ? () => onClick() : () => {}}>
            <Menu.Item key="visastatus">
                <Link to="/">{t("visaStatus")}</Link>
            </Menu.Item>
            <Menu.Item key="sysinfo">
                <Link to="/sysinfo">{t("sysStatus")}</Link>
            </Menu.Item>
            <Menu.Item key="checkee">
                <a href="https://checkee.info/" target="_blank" rel="noreferrer">
                    {t("checkee")}
                </a>
            </Menu.Item>
        </Menu>
    );
};
NavMenu.propTypes = {
    mode: PropTypes.oneOf(["vertical", "horizontal", "inline"]),
    theme: PropTypes.oneOf(["dark", "light"]),
    onClick: PropTypes.func,
};

const NavMenuPopover = () => {
    const [menuPop, setMenuPop] = useState(false);

    return (
        <Popover
            content={<NavMenu mode="vertical" theme="light" onClick={() => setMenuPop(!menuPop)} />}
            visible={menuPop}
            overlayStyle={{ minWidth: "65vw" }}
            trigger="click"
            placement="bottomRight"
            arrowPointAtCenter
        >
            <Button
                onClick={() => setMenuPop(!menuPop)}
                size="large"
                icon={menuPop ? <CloseOutlined /> : <MenuOutlined />}
            />
        </Popover>
    );
};

const LanguageButton = () => {
    const { i18n } = useTranslation();
    useEffect(() => setCookie("i18next", i18n.language));
    return (
        <Button
            onClick={() => i18n.changeLanguage(i18n.language === "en" ? "zh" : "en")}
            size="large"
            shape="circle"
            icon={
                <div // simple hack, could be optimized
                    style={{
                        width: "100%",
                        height: "100%",
                        display: "flex",
                        justifyContent: "center",
                        alignItems: "center",
                    }}
                >
                    <IoLanguageOutline size="20px" />
                </div>
            }
        />
    );
};

// const NotifyButton = () => {
//     const [t] = useTranslation();
//     const checkNotify = () => {
//         try {
//             if (Notification.permission === "granted") {
//                 const notification = new Notification(t("notificationInitTitle"), {
//                     body: t("notificationInitContent"),
//                 });
//             } else if (Notification.permission !== "denied") {
//                 Notification.requestPermission().then(permission => {
//                     if (permission === "granted") {
//                         const notification = new Notification(t("notificationInitTitle"), {
//                             body: t("notificationInitContent"),
//                         });
//                     } else {
//                         alert("still not enable, TODO: https");
//                     }
//                 });
//             } else {
//                 alert(t("notificationBlocked"));
//             }
//         } catch (e) {
//             alert(t("notificationNoSupport"));
//         }
//     };
//     return <Button size="large" shape="circle" icon={<BellOutlined />} onClick={() => checkNotify()} />;
// };

export default function Nav() {
    const screenXS = useScreenXS();

    const Logo = () => (
        <div className="logo" style={{ justifyContent: screenXS ? "center" : "flex-start" }}>
            <img src="/favicon.ico" height="40" width="40" alt="real tuixue logo" />
            <img src="/tuixue-logo.png" height="48" width="96" alt="fake tuixue logo" />
        </div>
    );

    return (
        <Header className="tuixue-header">
            <Row>
                <Col
                    xs={{ span: 24, push: 0 }}
                    sm={{ span: 24, push: 0 }}
                    md={{ span: 20, push: 2 }}
                    lg={{ span: 16, push: 4 }}
                    xl={{ span: 14, push: 5 }}
                >
                    <Row justify="center">
                        <Col xs={{ span: 4 }} md={0}>
                            <div className="center-box">
                                <NavMenuPopover />
                            </div>
                        </Col>
                        <Col xs={{ span: 16 }} md={{ span: 5 }}>
                            <Logo />
                        </Col>
                        <Col xs={0} md={{ span: 17 }}>
                            <NavMenu mode="horizontal" />
                        </Col>
                        <Col xs={{ span: 4 }} md={{ span: 2 }}>
                            <div className="center-box">
                                <LanguageButton />
                            </div>
                        </Col>
                    </Row>
                </Col>
            </Row>
        </Header>
    );
}
