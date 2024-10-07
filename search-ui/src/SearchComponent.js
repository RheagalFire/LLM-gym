import React, { useState, useEffect, useCallback } from 'react';
import Doodle from './assets/doodle_2.svg'; // Corrected import path

// Debounce function to delay the execution of a function
const debounce = (func, delay) => {
    let timeoutId;
    return (...args) => {
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        timeoutId = setTimeout(() => {
            func(...args);
        }, delay);
    };
};

function SearchComponent() {
    const [keyword, setKeyword] = useState('');
    const [results, setResults] = useState([]);

    const handleSearch = async (searchTerm) => {
        if (searchTerm.length < 3) {
            setResults([]); // Clear results if the keyword is less than 3 characters
            return;
        }
        try {
            const apiUrl = process.env.REACT_APP_API_BASE_URL || "http://localhost:8001";
            console.log("API URL:", apiUrl); // Log the API URL
            const response = await fetch(`${apiUrl}/api/v1/keyword_search?keyword=${searchTerm}&collection_name=LLM-gym`);
            if (!response.ok) {
                console.error(`HTTP error! status: ${response.status}`);
                const errorText = await response.text();
                console.error("Response text:", errorText);
                setResults([]); // Set results to an empty array in case of error
                return;
            }
            const data = await response.json();
            console.log("API Response:", data); // Log the API response
            setResults(data.hits || []);
        } catch (error) {
            console.error("Error fetching data:", error);
            setResults([]); // Set results to an empty array in case of error
        }
    };

    // Create a debounced version of handleSearch
    const debouncedSearch = useCallback(debounce(handleSearch, 1200), []);

    useEffect(() => {
        debouncedSearch(keyword);
    }, [keyword, debouncedSearch]);

    return (
        <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            minHeight: '100vh', 
            background: 'linear-gradient(135deg, #a8c0ff, #3f2b96)', // Pastel blue gradient background
            color: '#ffffff', // White text
            fontFamily: 'Arial, sans-serif'
        }}>
            <img src={Doodle} alt="LLM-gym Doodle" style={{ marginBottom: '40px', width: '150px' }} />
            <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                backgroundColor: '#3f2b96', 
                borderRadius: '25px', 
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)', 
                padding: '10px 20px', 
                width: '60%', 
                maxWidth: '600px',
                transition: 'box-shadow 0.3s ease',
                ':hover': {
                    boxShadow: '0 6px 16px rgba(0, 0, 0, 0.7)'
                }
            }}>
                <input
                    type="text"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder="Enter keyword"
                    style={{ 
                        flex: 1, 
                        border: 'none', 
                        outline: 'none', 
                        fontSize: '16px', 
                        padding: '10px',
                        backgroundColor: 'transparent', // Make background transparent
                        color: '#ffffff',
                        marginRight: '10px' // Add some space between input and button
                    }}
                />
                <button 
                    onClick={() => handleSearch(keyword)} 
                    style={{ 
                        padding: '10px 20px', 
                        cursor: 'pointer', 
                        backgroundColor: '#ffffff', 
                        color: '#3f2b96', 
                        border: 'none', 
                        borderRadius: '20px', 
                        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.3)',
                        transition: 'background-color 0.3s ease',
                        ':hover': {
                            backgroundColor: '#e0e0e0'
                        }
                    }}
                >
                    Search
                </button>
            </div>
            <div style={{ marginTop: '40px', width: '80%', maxWidth: '800px' }}>
                {results.map((result, index) => (
                    <div key={index} style={{ marginBottom: '20px', borderBottom: '1px solid #ffffff', paddingBottom: '10px' }}>
                        <a href={result.parent_link} style={{ textDecoration: 'none', color: '#3f2b96', fontSize: '18px', fontWeight: 'bold' }}>
                            <span dangerouslySetInnerHTML={{ __html: result._formatted.parent_title }} />
                        </a>
                        <p style={{ color: '#ffffff', fontSize: '14px' }}>
                            <span dangerouslySetInnerHTML={{ __html: result._formatted.parent_summary }} />
                        </p>
                        <div style={{ marginTop: '10px', display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                            {result._formatted.parent_keywords.slice(0, 5).map((keyword, i) => (
                                <span key={i} style={{ 
                                    backgroundColor: '#3f2b96', 
                                    color: '#ffffff', 
                                    padding: '5px 10px', 
                                    borderRadius: '15px', 
                                    fontSize: '12px'
                                }}>
                                    <span dangerouslySetInnerHTML={{ __html: keyword }} />
                                </span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default SearchComponent;