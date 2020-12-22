import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { HashLink as Link } from "react-router-hash-link";
import { Row, Col, Button, Layout, Menu, Typography, Popover } from "antd";
import { MenuOutlined, CloseOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useDispatch } from "react-redux";
import { IoLanguageOutline } from "react-icons/io5";
import "./TuixueHeader.less";
import { setCookie } from "../utils/cookie";
import { updateLanguage } from "../redux/languageSlice";

const { Header } = Layout;
const { Title } = Typography;

const Logo = () => (
    <Col
        xs={{ span: 2, push: 5 }}
        md={{ span: 2, push: 2 }}
        lg={{ span: 2, push: 3 }}
        xl={{ span: 2, push: 4 }}
        className="logo"
    >
        <img src="/favicon.ico" height="40" alt="real tuixue logo" />
        <img src="/tuixue-logo.png" height="48" alt="fake tuixue logo" />
    </Col>
);

const NavMenu = ({ mode, theme, onClick }) => {
    const [t, i18n] = useTranslation();
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
    const dispatch = useDispatch();
    const [t, i18n] = useTranslation();
    useEffect(() => {
        setCookie("i18next", i18n.language);
        dispatch(updateLanguage({ language: i18n.language }));
    });
    return (
        <Button
            onClick={() => i18n.changeLanguage(i18n.language === "en" ? "zh" : "en")}
            size="large"
            shape="circle"
            icon={<IoLanguageOutline />}
        />
    );
};

export default function Nav() {
    return (
        <Header className="tuixue-header">
            <Row>
                <Col xs={{ span: 2, push: 1 }} md={0}>
                    <NavMenuPopover />
                </Col>
                <Logo />
                <Col xs={0} md={{ span: 14, push: 6 }}>
                    <NavMenu mode="horizontal" />
                </Col>
                <Col xs={{ span: 2, push: 17 }} md={{ span: 2, push: 5 }} lg={{ span: 2, push: 3 }}>
                    <LanguageButton />
                </Col>
            </Row>
        </Header>
    );
}
