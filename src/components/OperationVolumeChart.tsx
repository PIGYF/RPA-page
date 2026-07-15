import { useEffect, useRef, type FC } from 'react';
import * as echarts from 'echarts';
import type { DateRange, OperationVolumePoint } from '../types';

interface OperationVolumeChartProps {
  range: DateRange;
  data: OperationVolumePoint[];
  onRangeChange: (range: DateRange) => void;
}

const ranges: DateRange[] = [7, 14, 30];

export const OperationVolumeChart: FC<OperationVolumeChartProps> = ({
  range,
  data,
  onRangeChange
}) => {
  const chartContainerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<echarts.EChartsType | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) {
      return undefined;
    }

    const chartInstance = echarts.init(chartContainerRef.current);
    chartRef.current = chartInstance;

    const resize = () => chartInstance.resize();
    const resizeObserver =
      typeof ResizeObserver !== 'undefined' ? new ResizeObserver(resize) : undefined;

    resizeObserver?.observe(chartContainerRef.current);
    window.addEventListener('resize', resize);

    return () => {
      resizeObserver?.disconnect();
      window.removeEventListener('resize', resize);
      chartInstance.dispose();
    };
  }, []);

  useEffect(() => {
    if (!chartRef.current) {
      return;
    }

    chartRef.current.setOption({
      backgroundColor: 'transparent',
      animationDuration: 600,
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(15, 23, 42, 0.96)',
        borderColor: 'rgba(148, 163, 184, 0.3)',
        textStyle: {
          color: '#e2e8f0'
        }
      },
      legend: {
        top: 0,
        right: 0,
        textStyle: {
          color: '#cbd5e1'
        }
      },
      grid: {
        top: 48,
        left: 20,
        right: 20,
        bottom: 16,
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: data.map((item) => item.label),
        axisLine: {
          lineStyle: {
            color: 'rgba(148, 163, 184, 0.24)'
          }
        },
        axisLabel: {
          color: '#94a3b8'
        }
      },
      yAxis: [
        {
          type: 'value',
          axisLabel: {
            color: '#94a3b8'
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(148, 163, 184, 0.14)'
            }
          }
        },
        {
          type: 'value',
          axisLabel: {
            color: '#94a3b8'
          },
          splitLine: {
            show: false
          }
        }
      ],
      series: [
        {
          name: '创建量',
          type: 'bar',
          barWidth: 14,
          itemStyle: {
            color: '#2dd4bf',
            borderRadius: [6, 6, 0, 0]
          },
          data: data.map((item) => item.created)
        },
        {
          name: '完成量',
          type: 'bar',
          barWidth: 14,
          itemStyle: {
            color: '#60a5fa',
            borderRadius: [6, 6, 0, 0]
          },
          data: data.map((item) => item.completed)
        },
        {
          name: '异常量',
          type: 'line',
          yAxisIndex: 1,
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            width: 3,
            color: '#f97316'
          },
          itemStyle: {
            color: '#f97316'
          },
          areaStyle: {
            color: 'rgba(249, 115, 22, 0.12)'
          },
          data: data.map((item) => item.exceptions)
        }
      ]
    });
  }, [data]);

  const createdTotal = data.reduce((sum, item) => sum + item.created, 0);

  return (
    <section className="chart-panel card">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Operation Volume</p>
          <h3>业务量与异常趋势</h3>
        </div>

        <div className="panel-actions">
          <div className="range-toggle">
            {ranges.map((item) => (
              <button
                key={item}
                type="button"
                className={item === range ? 'active' : ''}
                onClick={() => onRangeChange(item)}
              >
                {item} 天
              </button>
            ))}
          </div>

          <div className="panel-total">
            <span>总创建量</span>
            <strong>{createdTotal}</strong>
          </div>
        </div>
      </div>

      <div ref={chartContainerRef} className="chart-canvas" />
    </section>
  );
};
