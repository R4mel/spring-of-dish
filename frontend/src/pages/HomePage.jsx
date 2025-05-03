import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import IngredientItem from '../components/IngredientItem/IngredientItem';
import ingredientsData from '../data/IngredientData';

export default function HomePage() {
  const [selectedItems, setSelectedItems] = useState([]);
  const navigate = useNavigate();

  const toggleItem = (name) => {
    setSelectedItems((prev) =>
      prev.includes(name) ? prev.filter((n) => n !== name) : [...prev, name]
    );
  };

  const handleApply = () => {
    navigate('/fridge', { state: { fridgeItems: selectedItems } });
  };

  return (
    <div>
      <h3>재료 선택</h3>
      <div className="ingredientList">
        {ingredientsData.map((ing) => (
          <IngredientItem
            key={ing.name}
            name={ing.name}
            icon={ing.icon}
            selected={selectedItems.includes(ing.name)}
            onClick={() => toggleItem(ing.name)}
          />
        ))}
      </div>
      <button onClick={handleApply} disabled={selectedItems.length === 0}>
        적용하기
      </button>
    </div>
  );
}
