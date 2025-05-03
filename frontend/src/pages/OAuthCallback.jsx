import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

export default function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const code = searchParams.get('code');
  const error = searchParams.get('error');

  useEffect(() => {
    if (error) {
      console.error('카카오 로그인 실패:', error);
      return;
    }
    if (!code) {
      console.error('code가 없습니다.');
      return;
    }

    // TODO: 여기서 백엔드에 code를 넘겨서 최종 토큰+유저 정보를 받아올 수 있도록 호출하세요.
    // 예시:
    fetch('http://localhost:8000/redirect?code=' + code, {
      method: 'GET',
      credentials: 'include',
    })
      .then(res => res.json())
      .then(json => {
        console.log('백엔드 응답:', json);
        // 로그인 처리: 받은 JWT를 로컬스토리지 등에 저장하고
        // 메인 화면으로 리다이렉트
        localStorage.setItem('jwt', json.access_token);
        navigate('/');
      })
      .catch(err => {
        console.error('로그인 처리 중 에러:', err);
      });
  }, [code, error, navigate]);

  return (
    <div style={{ textAlign: 'center', marginTop: 100 }}>
      <p>로그인 처리 중...</p>
    </div>
  );
}