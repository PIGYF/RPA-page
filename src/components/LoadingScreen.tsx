import type { FC } from 'react';

interface LoadingScreenProps {
  label: string;
}

export const LoadingScreen: FC<LoadingScreenProps> = ({ label }) => (
  <div className="loading-screen">
    <div className="loading-orb" />
    <h2>AI Employee SAP Operations Center</h2>
    <p>{label}</p>
  </div>
);
