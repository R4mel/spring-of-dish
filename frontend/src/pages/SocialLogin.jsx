/*아직 카카오로그인페이지는 미확정 로그인 페이지 보지말기*/
import React from 'react';
import KakaoLoginButton from './KakaoLoginButton';

const SocialLogin = () => {
  return (
    <div style={styles.wrapper}>
      <div style={styles.box}>
      <h1 style={styles.brand}>cook's spring</h1>
      <p style={styles.subtitle}>간편하게 로그인하고<br /> 나만의 레시피와 재료 서비스를 이용해보세요</p>
        <KakaoLoginButton />
      </div>
    </div>
  );
};

const styles = {
  wrapper: {
    height: '100vh',
    backgroundColor: '#fff',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  box: {
    width: '360px',
    padding: '40px',
    backgroundColor: '#fff',
    borderRadius: '12px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
    textAlign: 'center',
  },
  title: {
    fontSize: '20px',
    fontWeight: '400',
    marginBottom: '30px',
    color: '#333',
    lineHeight: '1.5',
  },
};

export default SocialLogin;
