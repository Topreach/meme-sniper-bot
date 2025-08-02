package com.sniperbot.dashboard.controller;

import com.sniperbot.dashboard.model.WalletBalance;
import com.sniperbot.dashboard.service.WalletService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/wallet")
public class WalletController {

    @Autowired
    private WalletService walletService;

    @GetMapping("/balance")
    public WalletBalance getWalletBalance() {
        return walletService.getWalletBalance();
    }

    @PostMapping("/withdraw")
    public String requestWithdrawal(
            @RequestParam double amount,
            @RequestParam String address) {
        return walletService.requestWithdrawal(amount, address);
    }
}
