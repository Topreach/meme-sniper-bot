package com.sniperbot.dashboard.service;

import com.sniperbot.dashboard.model.Trade;
import com.sniperbot.dashboard.repository.TradeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class TradeService {

    @Autowired
    private TradeRepository tradeRepository;

    public List<Trade> getRecentTrades(int count) {
        return tradeRepository.findTopNByOrderByTimestampDesc(count);
    }

    public Map<String, Double> getDailyProfit() {
        Map<String, Double> dailyProfit = new HashMap<>();
        List<Object[]> results = tradeRepository.findDailyProfit();
        
        for (Object[] result : results) {
            LocalDate date = (LocalDate) result[0];
            Double profit = (Double) result[1];
            dailyProfit.put(date.toString(), profit);
        }
        
        return dailyProfit;
    }

    public double getCumulativeProfit() {
        Double profit = tradeRepository.sumProfit();
        return profit != null ? profit : 0.0;
    }
}
