import { useEffect, useState, type FC } from 'react';
import placeholderImage from '../assets/ai-employee-placeholder.svg';
import type { AiEmployeeProfile } from '../types';
import { StatusIcon } from './StatusIcon';

interface AiEmployeePanelProps {
  employee: AiEmployeeProfile;
  updatedAt: string;
}

const candidateSources = ['/ai-employee.gif', '/ai-employee.png'];

export const AiEmployeePanel: FC<AiEmployeePanelProps> = ({ employee, updatedAt }) => {
  const [imageSource, setImageSource] = useState<string>(placeholderImage);

  useEffect(() => {
    let active = true;

    const probeAsset = (index: number) => {
      if (index >= candidateSources.length) {
        if (active) {
          setImageSource(placeholderImage);
        }
        return;
      }

      const image = new Image();
      image.onload = () => {
        if (active) {
          setImageSource(candidateSources[index]);
        }
      };
      image.onerror = () => probeAsset(index + 1);
      image.src = candidateSources[index];
    };

    probeAsset(0);

    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="ai-employee-panel card">
      <div className="employee-visual">
        <img src={imageSource} alt="AI employee avatar" className="employee-image" />
      </div>

      <div className="employee-copy">
        <div className="employee-badge">
          <StatusIcon tone={employee.status} />
          <span>{employee.role}</span>
        </div>

        <h2>{employee.name}</h2>
        <p className="employee-greeting">{employee.greeting}</p>
        <p className="employee-description">{employee.description}</p>

        <div className="employee-tags">
          {employee.specialties.map((specialty) => (
            <span key={specialty} className="tag">
              {specialty}
            </span>
          ))}
        </div>

        <div className="employee-footer">
          <div>
            <span>重点关注</span>
            <strong>{employee.queueFocus}</strong>
          </div>
          <div>
            <span>刷新时间</span>
            <strong>{updatedAt}</strong>
          </div>
          <div>
            <span>服务承诺</span>
            <strong>{employee.responseSla}</strong>
          </div>
        </div>
      </div>
    </section>
  );
};
