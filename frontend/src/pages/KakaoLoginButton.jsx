/*아직 카카오로그인페이지는 미확정 로그인 페이지 보지말기*/
import React from 'react';

const KakaoLoginButton = () => {
  const handleLogin = () => {
    alert('카카오 로그인 연동 예정!');
  };

  return (
    <button onClick={handleLogin} style={styles.button}>
      <img
        src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/kakaotalk.svg"
        alt="kakao"
        style={styles.icon}
      />
      카카오 로그인
    </button>
  );
};

const styles = {
  button: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#FEE500',
    color: '#000',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '600',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    cursor: 'pointer',
  },
  icon: {
    width: '20px',
    height: '20px',
  },
  brand: {
    fontFamily: "'Playfair Display', serif",
    fontSize: '32px',
    fontWeight: '700',
    color: '#222',
    marginBottom: '12px',
  },
  
  subtitle: {
    fontSize: '16px',
    color: '#555',
    lineHeight: '1.5',
    marginBottom: '30px',
  }  
};

export default KakaoLoginButton;
