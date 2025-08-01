package com.sniperbot.dashboard.controller;

import com.sniperbot.dashboard.service.ProfitService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/profit")
public class ProfitController {

    @Autowired
    private ProfitService profitService;

    @GetMapping("/daily")
    public Map<String, Double> getDailyProfit() {
        return profitService.getDailyProfit();
    }

    @GetMapping("/weekly")
    public Map<String, Double> getWeeklyProfit() {
        return profitService.getWeeklyProfit();
    }

    @GetMapping("/cumulative")
    public double getCumulativeProfit() {
        return profitService.getCumulativeProfit();
    }
}
