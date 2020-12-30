import PropTypes from "prop-types";

export const overviewAttrProps = {
    visaType: PropTypes.string.isRequired,
    embassyCode: PropTypes.string.isRequired,
    earliestDate: PropTypes.arrayOf(PropTypes.string).isRequired,
    latestDate: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export const newestOverviewProps = {
    newest: PropTypes.shape({
        writeTime: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
        availableDate: PropTypes.arrayOf(PropTypes.string).isRequired,
    }),
};

export const overviewProps = {
    overview: PropTypes.shape(overviewAttrProps).isRequired,
};
