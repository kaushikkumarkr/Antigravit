
declare module 'react-plotly.js' {
    import React from 'react';
    import { Layout, Data, Config } from 'plotly.js';

    interface PlotlyEditorProps {
        graphDiv?: HTMLElement;
        onInitialized?: (figure: any, graphDiv: HTMLElement) => void;
        onUpdate?: (figure: any, graphDiv: HTMLElement) => void;
        data?: Data[];
        layout?: Partial<Layout>;
        config?: Partial<Config>;
        frames?: any[];
        style?: React.CSSProperties;
        useResizeHandler?: boolean;
        debug?: boolean;
        className?: string;
        onPurge?: (figure: any, graphDiv: HTMLElement) => void;
        onError?: (err: any) => void;
    }

    const Plot: React.FC<PlotlyEditorProps>;
    export default Plot;
}

declare module 'plotly.js' {
    export interface Layout {
        [key: string]: any;
    }
    export interface Data {
        [key: string]: any;
    }
    export interface Config {
        [key: string]: any;
    }
}
