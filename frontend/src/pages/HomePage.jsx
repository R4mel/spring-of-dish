// src/pages/HomePage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import IngredientItem from '../components/IngredientItem/IngredientItem';
import ingredientsData from '../data/IngredientData';
import {
  authorize,
  getProfile,
  getMessage,
  logout,
  unlink,
} from '../api';

export default function HomePage() {
  const [selectedItems, setSelectedItems] = useState([]);
  const [user, setUser]         = useState(null);
  const [message, setMessage]   = useState('');
  const navigate = useNavigate();

  // 마운트 시 프로필·메시지 가져오기
  useEffect(() => {
    getProfile()
      .then(data => setUser(data))
      .catch(() => setUser(null));
    getMessage()
      .then(data => setMessage(data.message || ''))
      .catch(() => {});
  }, []);

  const toggleItem = (name) => {
    setSelectedItems(prev =>
      prev.includes(name)
        ? prev.filter(n => n !== name)
        : [...prev, name]
    );
  };

  const handleApply = () => {
    navigate('/fridge', { state: { selectedIngredients: selectedItems } });
  };

  return (
    <div>
      {!user ? (
        <button onClick={authorize}>카카오 로그인</button>
      ) : (
        <>
          <p>안녕하세요, {user.nickname}님</p>
          {message && <p>📬 {message}</p>}
          <button onClick={() => navigate('/profile')}>내 프로필</button>
          <button onClick={() => navigate('/message')}>메시지 확인</button>
          <button onClick={logout}>로그아웃</button>
          <button onClick={unlink}>계정 연결 해제</button>
        </>
      )}

      <h3>재료 선택</h3>
      <div className="ingredientList">
        {ingredientsData.map(ing => (
          <IngredientItem
            key={ing.name}
            name={ing.name}
            icon={ing.icon}
            selected={selectedItems.includes(ing.name)}
            onClick={() => toggleItem(ing.name)}
          />
        ))}
      </div>
      <button
        onClick={handleApply}
        disabled={selectedItems.length === 0}
      >
        적용하기
      </button>
    </div>
  );
}
