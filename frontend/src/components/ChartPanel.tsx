
import React from 'react';
import Plot from 'react-plotly.js';
import type { Layout } from 'plotly.js';

interface ChartPanelProps {
    visualization: any;
}

export const ChartPanel: React.FC<ChartPanelProps> = ({ visualization }) => {
    if (!visualization) {
        return (
            <div className="h-full flex items-center justify-center text-slate-500 bg-slate-900 border-l border-slate-800 p-8 text-center">
                <div>
                    <p className="text-lg font-medium mb-2">No Visualization</p>
                    <p className="text-sm">Ask for a chart or trend to see data here.</p>
                </div>
            </div>
        );
    }

    // Merge default dark theme layout
    const darkLayout: Partial<Layout> = {
        paper_bgcolor: '#0f172a', // slate-900
        plot_bgcolor: '#0f172a',
        font: {
            color: '#e2e8f0', // slate-200
            family: 'Inter, sans-serif'
        },
        ...visualization.layout,
        autosize: true,
        margin: { t: 40, r: 20, b: 40, l: 60 },
    };

    return (
        <div className="h-full bg-slate-900 border-l border-slate-800 flex flex-col">
            <div className="p-4 border-b border-slate-800">
                <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Visualization</h2>
            </div>
            <div className="flex-1 w-full h-full p-4 relative">
                {/* Container size hacking for Plotly responsiveness */}
                <div className="absolute inset-0 p-4">
                    <Plot
                        data={visualization.data}
                        layout={darkLayout}
                        useResizeHandler={true}
                        style={{ width: '100%', height: '100%' }}
                        config={{ responsive: true, displayModeBar: false }}
                    />
                </div>
            </div>
        </div>
    );
};
