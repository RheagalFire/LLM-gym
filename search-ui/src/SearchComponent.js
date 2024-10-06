import React, { useState, useEffect, useCallback } from 'react';

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

    const truncateContent = (content, maxLength) => {
        if (content.length > maxLength) {
            return content.substring(0, maxLength) + '...';
        }
        return content;
    };

    return (
        <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            minHeight: '100vh', 
            background: 'linear-gradient(to bottom, rgba(224, 247, 250, 1), rgba(224, 247, 250, 0.5))', // Gradient background
            color: '#333',
            fontFamily: 'Arial, sans-serif'
        }}>
            <h1 style={{ marginBottom: '40px', color: '#007BFF' }}>LLM-gym</h1>
            <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                backgroundColor: '#ffffff', 
                borderRadius: '25px', 
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', 
                padding: '10px 20px', 
                width: '60%', 
                maxWidth: '600px'
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
                        padding: '10px'
                    }}
                />
                <button 
                    onClick={() => handleSearch(keyword)} 
                    style={{ 
                        padding: '10px 20px', 
                        cursor: 'pointer', 
                        backgroundColor: '#007BFF', 
                        color: '#fff', 
                        border: 'none', 
                        borderRadius: '20px', 
                        marginLeft: '10px'
                    }}
                >
                    Search
                </button>
            </div>
            <div style={{ marginTop: '40px', width: '80%', maxWidth: '800px' }}>
                {results.map((result, index) => (
                    <div key={index} style={{ marginBottom: '20px', borderBottom: '1px solid #ccc', paddingBottom: '10px' }}>
                        <a href={result.parent_link} style={{ textDecoration: 'none', color: '#007BFF', fontSize: '18px' }}>
                            {result.parent_title}
                        </a>
                        <p style={{ color: '#666', fontSize: '14px' }}>
                            {truncateContent(result.parent_content, 500)}
                        </p>
                        <div style={{ marginTop: '10px', display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                            {result.parent_keywords.slice(0, 5).map((keyword, i) => (
                                <span key={i} style={{ 
                                    backgroundColor: '#007BFF', 
                                    color: '#fff', 
                                    padding: '5px 10px', 
                                    borderRadius: '15px', 
                                    fontSize: '12px'
                                }}>
                                    {keyword}
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