import React from 'react';
import { Spin } from 'antd';

const Loading = ({ tip = 'Đang tải...' }) => {
    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100%',
            minHeight: 200,
            padding: 24,
        }}>
            <Spin size="large" tip={tip} />
        </div>
    );
};

export default Loading;
