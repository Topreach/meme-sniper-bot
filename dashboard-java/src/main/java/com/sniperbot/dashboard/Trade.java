package com.sniperbot.dashboard.model;

import javax.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
public class Trade {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String tokenAddress;
    private BigDecimal amountEth;
    private BigDecimal tokenAmount;
    private BigDecimal profitEth;
    private LocalDateTime timestamp;
    
    // Getters and setters
}
